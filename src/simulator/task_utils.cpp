// Copyright (c) Facebook, Inc. and its affiliates.
//
// Licensed under the Apache License, Version 2.0 (the "License");
// you may not use this file except in compliance with the License.
// You may obtain a copy of the License at
//
//     http://www.apache.org/licenses/LICENSE-2.0
//
// Unless required by applicable law or agreed to in writing, software
// distributed under the License is distributed on an "AS IS" BASIS,
// WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
// See the License for the specific language governing permissions and
// limitations under the License.
#include "task_utils.h"
#include "task_validation.h"
#include "thrift_box2d_conversion.h"

#include <iostream>


bool print_step = false;
bool first = true;
bool first_collision = true;
bool first_force = true;
int gbl_step = 0;

namespace {
struct SimulationRequest {
  int maxSteps;
  int stride;
};

class contactAppend : public b2ContactListener {
    std::set<b2Contact*> contact_list;

    void BeginContact(b2Contact* contact) {
        const b2Body* body1 = nullptr;
        const b2Body* body2 = nullptr;

        // check fixture A
        const b2Body* box2dBody_A = contact->GetFixtureA()->GetBody();
        Box2dData* box2d_data_A = static_cast<Box2dData*>(box2dBody_A->GetUserData());
        body1 = box2dBody_A;
        // check fixture B
        const b2Body* box2dBody_B = contact->GetFixtureB()->GetBody();
        Box2dData* box2d_data_B = static_cast<Box2dData*>(box2dBody_B->GetUserData());
        body2 = box2dBody_B;
        // box2d_data_A->object_type == 2 --> USER OBJECT
        if (!print_step) {
            if (first) {
              first = false;
            } else {
              std::cout << ", ";
            }
            std::cout << "{\"step\": " << gbl_step << ", \"collisions\": [";
            print_step = true;
        }
        if (first_collision) {
          first_collision = false;
        } else {
          std::cout << ", ";
        }
        std::cout << "{\"kind\": \"begin\", ";
        std::cout <<"\"1\": {";
        std::cout << "\"id\": " << box2d_data_A->object_id << ", \"type\": " << box2d_data_A->object_type << ", \"x\": " << body1->GetWorldCenter().x << ", \"y\": " << body1->GetWorldCenter().y;
        std::cout << ", \"x_vel\": " << body1->GetLinearVelocity().x << ", \"y_vel\": " << body1->GetLinearVelocity().y << ", \"angle\": " << body1->GetAngle();
        std::cout << "}, \"2\": {";
        std::cout << "\"id\": " << box2d_data_B->object_id << ", \"type\": " << box2d_data_B->object_type << ", \"x\": " << body2->GetWorldCenter().x << ", \"y\": " << body2->GetWorldCenter().y;
        std::cout << ", \"x_vel\": " << body2->GetLinearVelocity().x << ", \"y_vel\": " << body2->GetLinearVelocity().y << ", \"angle\": " << body2->GetAngle();
        std::cout << "}}";
    }


    void EndContact(b2Contact* contact) {
        const b2Body* body1 = nullptr;
        const b2Body* body2 = nullptr;

        // check fixture A
        const b2Body* box2dBody_A = contact->GetFixtureA()->GetBody();
        Box2dData* box2d_data_A = static_cast<Box2dData*>(box2dBody_A->GetUserData());
        body1 = box2dBody_A;
        // check fixture B
        const b2Body* box2dBody_B = contact->GetFixtureB()->GetBody();
        Box2dData* box2d_data_B = static_cast<Box2dData*>(box2dBody_B->GetUserData());
        body2 = box2dBody_B;

        if (!print_step) {
            if (first) {
              first = false;
            } else {
              std::cout << ", ";
            }
            std::cout << "{\"step\": " << gbl_step << ", \"collisions\": [";
            print_step = true;
        }
        if (first_collision) {
          first_collision = false;
        } else {
          std::cout << ", ";
        }
        std::cout << "{\"kind\": \"end\", ";
        std::cout <<"\"1\": {";
        std::cout << "\"id\": " << box2d_data_A->object_id << ", \"type\": " << box2d_data_A->object_type << ", \"x\": " << body1->GetWorldCenter().x << ", \"y\": " << body1->GetWorldCenter().y;
        std::cout << ", \"x_vel\": " << body1->GetLinearVelocity().x << ", \"y_vel\": " << body1->GetLinearVelocity().y << ", \"angle\": " << body1->GetAngle();
        std::cout << "}, \"2\": {";
        std::cout << "\"id\": " << box2d_data_B->object_id << ", \"type\": " << box2d_data_B->object_type << ", \"x\": " << body2->GetWorldCenter().x << ", \"y\": " << body2->GetWorldCenter().y;
        std::cout << ", \"x_vel\": " << body2->GetLinearVelocity().x << ", \"y_vel\": " << body2->GetLinearVelocity().y << ", \"angle\": " << body2->GetAngle();
        std::cout << "}}";
        contact_list.erase(contact);
    }

    /*void PostSolve(b2Contact* contact, const b2ContactImpulse* impulse) {
        const bool is_in = contact_list.find(contact) != contact_list.end();
        if (!is_in) {
            if (first_force) {
                std::cout << "], \"forces\": [";
            }
            contact_list.insert(contact);
            Box2dData* data = static_cast<Box2dData*>(contact->GetFixtureA()->GetBody()->GetUserData());
            std::cout << impulse->normalImpulses[0];
        }
    }*/
};


// Runs simulation for the scene. If task is not nullptr, is-task-solved checks
// are performed.
::task::TaskSimulation simulateTask(const ::scene::Scene &scene,
                                    const SimulationRequest &request,
                                    const ::task::Task *task, bool do_print) {
  std::unique_ptr<b2WorldWithData> world = convertSceneToBox2dWorld(scene, do_print);

  unsigned int continuousSolvedCount = 0;
  std::vector<::scene::Scene> scenes;
  std::vector<bool> solveStateList;
  bool solved = false;
  int step = 0;
  // For different relations number of steps the condition should hold varies.
  // For NOT_TOUCHING relation one of three should be true:
  //   1. Objects are touching at the beginning and then not touching for
  //   kStepsForSolution steps.
  //   2. Objects are not touching at the beginning, touching at some point of
  //   simulation and then not touching for kStepsForSolution steps.
  //   3. Objects are not touching whole sumulation.
  // For TOUCHING_BRIEFLY a single touching is allowed.
  // For all other relations the condition must hold for kStepsForSolution
  // consequent steps.
  bool lookingForSolution =
      (task == nullptr || !isTaskInSolvedState(*task, *world) ||
       task->relationships.size() != 1 ||
       task->relationships[0] != ::task::SpatialRelationship::NOT_TOUCHING);
  const bool allowInstantSolution =
      (task != nullptr && task->relationships.size() == 1 &&
       task->relationships[0] == ::task::SpatialRelationship::TOUCHING_BRIEFLY);

  contactAppend contactInstance;
  if (do_print) {
     world->SetContactListener(&contactInstance);
  }

  for (; step < request.maxSteps; step++) {
    print_step = false;
    gbl_step = step;
    // Instruct the world to perform a single step of simulation.
    // It is generally best to keep the time step and iterations fixed.
    first_collision = true;
    first_force = true;
    world->Step(kTimeStep, kVelocityIterations, kPositionIterations);
    if (print_step) std::cout << "]";

    bool did_list = false;
    bool first_step = true;
    for (b2Body* b = world->GetBodyList(); b; b = b->GetNext()) {
    	Box2dData* data = static_cast<Box2dData*>(b->GetUserData());
    	if (do_print && (b->GetType() == b2_dynamicBody)) {
        if (!print_step) {
            if (first) {
              first = false;
            } else {
              std::cout << ", ";
            }
            std::cout << "{\"step\": " << gbl_step;
            print_step = true;
        }
        if (!did_list) {
          std::cout << ", \"list\": [";
          did_list = true;
        }
        if (first_step) {
          first_step = false;
        } else {
          std::cout << ", ";
        }
    		std::cout << "{\"id\": " << data->object_id << ", \"type\": " << data->object_type << ", \"x\": " << b->GetWorldCenter().x << ", \"y\": " << b->GetWorldCenter().y;
 			std::cout << ", \"x_vel\": " << b->GetLinearVelocity().x << ", \"y_vel\": " << b->GetLinearVelocity().y << ", \"angle\": " << b->GetAngle() << "}";
 		}
	}

  if (did_list) std::cout << "]";
  if (print_step) std::cout << "}";
    if (request.stride > 0 && step % request.stride == 0) {
      scenes.push_back(updateSceneFromWorld(scene, *world));
    }
    if (task == nullptr) {
      solveStateList.push_back(false);
    } else {
      solveStateList.push_back(isTaskInSolvedState(*task, *world));
      if (solveStateList.back()) {
        continuousSolvedCount++;
        if (lookingForSolution) {
          if (continuousSolvedCount >= kStepsForSolution ||
              allowInstantSolution) {
            solved = true;
            break;
          }
        }
      } else {
        lookingForSolution = true;  // Task passed through non-solved state.
        continuousSolvedCount = 0;
      }
    }
  }

  if (!lookingForSolution && continuousSolvedCount == solveStateList.size()) {
    // See condition 3) for NOT_TOUCHING relation above.
    solved = true;
  }

  {
    std::vector<bool> stridedSolveStateList;
    if (request.stride > 0) {
      for (size_t i = 0; i < solveStateList.size(); i += request.stride) {
        stridedSolveStateList.push_back(solveStateList[i]);
      }
    }
    stridedSolveStateList.swap(solveStateList);
  }

  ::task::TaskSimulation taskSimulation;
  taskSimulation.__set_sceneList(scenes);
  taskSimulation.__set_stepsSimulated(step);
  if (task != nullptr) {
    taskSimulation.__set_solvedStateList(solveStateList);
    taskSimulation.__set_isSolution(solved);
  }

  std::cout << std::flush;

  return taskSimulation;
}
}  // namespace

std::vector<::scene::Scene> simulateScene(const ::scene::Scene &scene,
                                          const int num_steps) {
  const SimulationRequest request{num_steps, 1};
  const auto simulation = simulateTask(scene, request, /*task=*/nullptr, false);
  return simulation.sceneList;
}

::task::TaskSimulation simulateTask(const ::task::Task &task,
                                    const int num_steps, const int stride, bool do_print) {
  const SimulationRequest request{num_steps, stride};
  return simulateTask(task.scene, request, &task, do_print);
}
